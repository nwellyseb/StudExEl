from datetime import UTC, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)

from sqlalchemy import or_

from extensions import db

from forms.message_form import MessageForm

from models.conversation import Conversation
from models.item import Item
from models.message import Message

from utils.decorators import login_required


messages = Blueprint(
    "messages",
    __name__,
)


def get_unread_message_counts(user_id):

    unread_rows = db.session.execute(
        db.select(
            Message.conversation_id,
            db.func.count(Message.id),
        )
        .join(
            Conversation,
            Message.conversation_id
            == Conversation.id,
        )
        .where(
            Message.sender_id != user_id,
            Message.is_read.is_(False),
            or_(
                Conversation.buyer_id == user_id,
                Conversation.seller_id == user_id,
            ),
        )
        .group_by(
            Message.conversation_id
        )
    ).all()

    return {
        conversation_id: unread_count
        for conversation_id, unread_count
        in unread_rows
    }


@messages.app_context_processor
def inject_unread_message_count():

    user_id = session.get(
        "user_id"
    )

    if user_id is None:

        return {
            "unread_message_count": 0,
        }

    unread_counts = get_unread_message_counts(
        user_id
    )

    return {
        "unread_message_count": sum(
            unread_counts.values()
        ),
    }


@messages.route("/messages")
@login_required
def inbox():

    user_id = session["user_id"]

    conversations = Conversation.query.filter(
        or_(
            Conversation.buyer_id == user_id,
            Conversation.seller_id == user_id,
        )
    ).order_by(
        Conversation.updated_at.desc()
    ).all()

    unread_counts = get_unread_message_counts(
        user_id
    )

    return render_template(
        "messages/inbox.html",
        conversations=conversations,
        current_user_id=user_id,
        unread_counts=unread_counts,
    )


@messages.route(
    "/messages/start/<int:item_id>",
    methods=["POST"],
)
@login_required
def start_conversation(item_id):

    item = db.get_or_404(
        Item,
        item_id,
    )

    user_id = session["user_id"]

    if item.seller_id == user_id:

        flash(
            "You cannot message yourself about your own listing.",
            "warning",
        )

        return redirect(
            url_for(
                "marketplace.item_details",
                item_id=item.id,
            )
        )

    if item.status == "Sold":

        flash(
            "This item has already been sold.",
            "warning",
        )

        return redirect(
            url_for(
                "marketplace.item_details",
                item_id=item.id,
            )
        )

    conversation = Conversation.query.filter_by(
        item_id=item.id,
        buyer_id=user_id,
        seller_id=item.seller_id,
    ).first()

    if conversation is None:

        conversation = Conversation(
            item_id=item.id,
            buyer_id=user_id,
            seller_id=item.seller_id,
        )

        db.session.add(
            conversation
        )

        db.session.commit()

    return redirect(
        url_for(
            "messages.conversation",
            conversation_id=conversation.id,
        )
    )


@messages.route(
    "/messages/<int:conversation_id>",
    methods=["GET", "POST"],
)
@login_required
def conversation(conversation_id):

    conversation_data = db.get_or_404(
        Conversation,
        conversation_id,
    )

    user_id = session["user_id"]

    if user_id not in (
        conversation_data.buyer_id,
        conversation_data.seller_id,
    ):

        flash(
            "You cannot access this conversation.",
            "danger",
        )

        return redirect(
            url_for(
                "messages.inbox"
            )
        )

    form = MessageForm()

    unread_messages = Message.query.filter(
        Message.conversation_id
        == conversation_data.id,
        Message.sender_id != user_id,
        Message.is_read.is_(False),
    ).all()

    for unread_message in unread_messages:

        unread_message.is_read = True

    if unread_messages:

        db.session.commit()

    if form.validate_on_submit():

        body = form.body.data.strip()

        if not body:

            flash(
                "Enter a message before sending.",
                "warning",
            )

            return redirect(
                url_for(
                    "messages.conversation",
                    conversation_id=conversation_data.id,
                )
            )

        message = Message(
            conversation_id=conversation_data.id,
            sender_id=user_id,
            body=body,
        )

        conversation_data.updated_at = (
            datetime.now(UTC).replace(tzinfo=None)
        )

        db.session.add(
            message
        )

        db.session.commit()

        return redirect(
            url_for(
                "messages.conversation",
                conversation_id=conversation_data.id,
            )
        )

    conversation_messages = Message.query.filter_by(
        conversation_id=conversation_data.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return render_template(
        "messages/conversation.html",
        conversation=conversation_data,
        messages=conversation_messages,
        form=form,
        current_user_id=user_id,
    )