from flask import Blueprint, render_template, url_for, redirect, request, flash, make_response
import flask_login, io
from flask_login import current_user
from . import db
from matplotlib.pyplot import Figure
from .models import User, Influencer, Campaign, Ad_request
import datetime as dt


views=Blueprint("views",__name__)

# --------------------------------------------ADMIN Routes------------------------------------
@views.route("/admin home")
@flask_login.login_required
def admin_home():
    return render_template("admin_home.html",admin_name=current_user.name)


@views.route("/plot_users/plot.png")
@flask_login.login_required
def plot_users():
    roles=['Sponsor','Influencer']
    user_data=[db.session.query(User).filter_by(role=role).count() for role in roles]

    fig1 = Figure()
    ax = fig1.subplots()
    ax.bar(roles, user_data, color=['gold','orange'])
    ax.set_xlabel('Role')
    ax.set_ylabel('Number of Users')
    ax.set_title('Number of Users by Role')
    user_output1 = io.BytesIO()
    fig1.savefig(user_output1, format='png')
    user_output1.seek(0)
    return make_response(user_output1.getvalue(), 200, {'Content-Type': 'image/png'})


@views.route("/plot_campaigns/plot.png")
@flask_login.login_required
def plot_campaigns():
    visibility=['Public','Private']
    cpg_data=[db.session.query(Campaign).filter_by(visibility=visible).count() for visible in visibility]
    fig2 = Figure()
    ax = fig2.subplots()
    ax.bar(visibility, cpg_data, color=['magenta','red'])
    ax.set_xlabel('Campaign Visibility')
    ax.set_ylabel('Campaign')
    ax.set_title('Count')
    user_output2 = io.BytesIO()
    fig2.savefig(user_output2, format='png')
    user_output2.seek(0)
    return make_response(user_output2.getvalue(), 200, {'Content-Type': 'image/png'})

@views.route("/flag_user/<int:influ_id>",methods=['POST'])
@flask_login.login_required
def flag_influencer(influ_id):
    influ=Influencer.query.get_or_404(influ_id)
    influ.is_flag= not influ.is_flag
    db.session.commit()
    return redirect(url_for('views.show_influencers'))


@views.route("/admin_campaigns")
@flask_login.login_required
def show_campaigns():
    campaigns= Campaign.query.all()
    return render_template("admin_campaigns.html",campaigns=campaigns, admin_name=current_user.name)


@views.route("/show_influencers")
@flask_login.login_required
def show_influencers():
    influencers=Influencer.query.all()
    return render_template("admin_influencers.html",influencers=influencers,admin_name=current_user.name)


# --------------------------------------------Influencer Routes-------------------------------

@views.route("/influencer home")
@flask_login.login_required
def influ_home():
    new_influencer =Influencer.query.filter_by(user_id=current_user.usr_id).first()
    if new_influencer:
        if new_influencer.category is None and new_influencer.niche is None and new_influencer.reach is None:
            flash("Please update your profile before accepting requests", "warning")
            return redirect(url_for("views.edit_influ_profile",influencer_id=new_influencer.influencer_id))
    campaigns=Campaign.query.all()
    my_requests=Ad_request.query.filter_by(influencer_id=new_influencer.influencer_id).all()
    return render_template("influ_home.html",campaigns=campaigns,requests=my_requests,influ_name=current_user.name)


@views.route("/influencer profile")
@flask_login.login_required
def influ_profile():
    influencer = Influencer.query.filter_by(user_id=current_user.usr_id).first()
    return render_template('influ_profile.html',influencer=influencer, influ_name=current_user.name)


@views.route("/edit_influencer_profile/<int:influencer_id>", methods=['GET', 'POST'])
@flask_login.login_required
def edit_influ_profile(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    if request.method == 'POST':
        # Get the updated data from the form
        influencer.category = request.form.get('category')
        influencer.niche = request.form.get('niche')
        influencer.reach = request.form.get('reach')
        # Save changes to the database  
        db.session.commit()
        return redirect(url_for('views.influ_home'))
    return render_template('edit_influ_profile.html',influencer=influencer ,influ_name=current_user.name)


@views.route("/accept_request/<int:ad_id>", methods=['POST'])
@flask_login.login_required
def accept_request(ad_id):
    ad_request=Ad_request.query.get_or_404(ad_id)
    ad_request.status='Accepted'
    db.session.commit()
    flash("Request accepted!",category='success')
    return redirect(url_for('views.influ_home'))


@views.route("/reject_request/<int:ad_id>", methods=['POST'])
@flask_login.login_required
def reject_request(ad_id):
    ad_request=Ad_request.query.get_or_404(ad_id)
    ad_request.status='Rejected'
    db.session.commit()
    flash("Request rejected!",category='danger')
    return redirect(url_for('views.influ_home'))


@views.route('/search_campaigns',methods=['GET'])
@flask_login.login_required
def search_campaigns():
    query=  request.args.get('query','')
    new_influencer =Influencer.query.filter_by(user_id=current_user.usr_id).first()
    if query:
        campaign_search=f'%{query}%'
        campaign=Campaign.query.filter(
            (Campaign.campaign_name.ilike(campaign_search))|(Campaign.budget.ilike(campaign_search))|
            (Campaign.visibility.ilike(campaign_search))).all()
        my_requests=Ad_request.query.filter_by(influencer_id=new_influencer.influencer_id).all()
        return render_template('influ_home.html',campaigns=campaign, influ_name=current_user.name,requests=my_requests)
    else:
        return redirect(url_for('views.influ_home.html'))


# --------------------------------------------SPONSOR Routes----------------------------------

@views.route("/sponsor home")
@flask_login.login_required
def sponsor_home():
    campaigns=Campaign.query.all()
    influencers=Influencer.query.all()
    return render_template("sponsor_home.html",campaigns=campaigns, influencers=influencers, sponsor_name=current_user.name)


@views.route("/create_campaign", methods=['GET','POST'])
@flask_login.login_required
def create_campaign():
    if request.method=="POST":
        campaign_name=request.form['campaign_name']
        description=request.form['description']
        start_date=request.form['start_date']
        end_date=request.form['end_date']
        budget=request.form['budget']
        try:
            # Convert string dates to date objects
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template("create_campaign.html")

        try:
            # Convert budget to integer
            budget = int(request.form['budget'])
        except ValueError:
            flash('Budget must be a number.', 'danger')
            return render_template("create_campaign.html")
        visibility=request.form['visibility']
        cpg=Campaign(campaign_name=campaign_name,description=description,start_date=start_date,
                     end_date=end_date, budget=budget,
                     visibility=visibility, user_id=current_user.usr_id)
        db.session.add(cpg)
        db.session.commit()
        return redirect(url_for("views.sponsor_home"))
    return render_template("create_campaign.html",sponsor_name=current_user.name)


@views.route("/manage_my_campaigns")
@flask_login.login_required
def manage_campaigns():
    # return all the campaigns created by the current user
    my_campaigns=Campaign.query.filter_by(user_id=current_user.usr_id).all()
    return render_template('my_campaigns.html',campaigns=my_campaigns,sponsor_name=current_user.name)


@views.route("/edit_campaign/<int:campaign_id>",methods=['GET','POST'])
@flask_login.login_required
def edit_campaign(campaign_id):
    campaign=Campaign.query.get_or_404(campaign_id)

    #checking if the campaign belongs to current user or not
    if campaign.user_id!=current_user.usr_id:
        flash("You are not the author of this campaign","danger")
        return redirect(url_for("views.manage_campaigns"))
    if request.method=='POST':
        campaign.campaign_name=request.form['campaign_name']
        campaign.description=request.form['description']
        campaign.start_date = dt.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = dt.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        campaign.budget = int(request.form['budget'])
        campaign.visibility = request.form['visibility']
        db.session.commit()
        return redirect(url_for("views.manage_campaigns"))
    return render_template("edit_campaigns.html",campaign=campaign,sponsor_name=current_user.name)


@views.route("/delete_campaign/<int:campaign_id>",methods=['GET','POST'])
@flask_login.login_required
def delete_campaign(campaign_id):
    campaign=Campaign.query.get_or_404(campaign_id)
    #checking if the campaign belongs to current user or not
    if campaign.user_id!=current_user.usr_id:
        flash("You are not the author of this campaign","danger")
    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('views.manage_campaigns'))


@views.route('/search',methods=['GET'])
@flask_login.login_required
def search_influencers():
    query=  request.args.get('query','')
    if query:
        influ_search=f'%{query}%'
        influencers=Influencer.query.filter(
            (Influencer.name.ilike(influ_search))|(Influencer.category.ilike(influ_search))|
            (Influencer.niche.ilike(influ_search))|(Influencer.reach.ilike(influ_search))).all()
        campaigns=Campaign.query.all()
        return render_template('sponsor_home.html', influencers=influencers,campaigns=campaigns,sponsor_name=current_user.name)
    else:
        return redirect(url_for('views.sponsor_home'))
    

@views.route("/send request/<int:influ_id>",methods=['GET','POST'])
@flask_login.login_required
def send_request(influ_id):
    influencer=Influencer.query.get_or_404(influ_id)
    cpg = Campaign.query.filter_by(user_id=current_user.usr_id).all()

    if request.method=='POST':
        cpg_id=request.form['campaign_id']
        msg = request.form['message']
        req = request.form['requirements']
        pmt = request.form['payment']
        status = request.form.get('status', 'pending')

        sp_id=current_user.usr_id

        new_request=Ad_request(sponsor_id=sp_id, campaign_id=cpg_id,
                               influencer_id=influ_id,message=msg,
                               requirements=req,amount=pmt,status=status)
        try:
            db.session.add(new_request)
            db.session.commit()
            flash("Request created and sent successfully!" ,category='success')
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('views.sponsor_home'))
    return render_template('send_request.html',influencer=influencer,campaigns=cpg, sponsor_name=current_user.name)
    

@views.route('/manage_reuqests',methods=['GET'])
@flask_login.login_required
def manage_requests():
    # return all the campaigns created by the current user
    my_requests=Ad_request.query.filter_by(sponsor_id=current_user.usr_id).all()
    return render_template('manage_request.html',ad_requests=my_requests,sponsor_name=current_user.name)


@views.route('/edit_request/<int:ad_id>',methods=['GET','POST'])
@flask_login.login_required
def edit_request(ad_id):
    get_request=Ad_request.query.get_or_404(ad_id)

    # Fetch the influencer related to this ad request
    influencer = Influencer.query.get(get_request.influencer_id)

    if request.method=='POST':
        get_request.message=request.form['message']
        get_request.requirements=request.form['requirements']
        get_request.amount=request.form['payment']
        get_request.status=request.form.get('status', 'pending')
        db.session.commit()
        return redirect(url_for('views.manage_requests'))
    return render_template('edit_request.html',my_request=get_request,sponsor_name=current_user.name,influencer=influencer)

@views.route("/delete_request/<int:request_id>",methods=['GET','POST'])
@flask_login.login_required
def delete_request(request_id):
    ad_request=Ad_request.query.get_or_404(request_id)
    #checking if the campaign belongs to current user or not
    if ad_request.sponsor_id!=current_user.usr_id:
        flash("You are not the author of this request","danger")
    db.session.delete(ad_request)
    db.session.commit()
    flash("Request Deleted Successfully",category='success')
    return redirect(url_for('views.manage_requests'))

